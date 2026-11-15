EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.58)
	}

	GenType("continous")

	ParticleRate()
	{
		keyf(0, 160)
		keyf(0.144, 120)
		keyf(0.18, 0)
	}

	StartVelocity()
	{
		keyf(0, 190)
		keyf(0.09, 161.5)
		keyf(0.18, 114)
	}

	StartVelocityRand()
	{
		keyv(0, 7.6, 9.5, 7.6)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.25)
	}
}
