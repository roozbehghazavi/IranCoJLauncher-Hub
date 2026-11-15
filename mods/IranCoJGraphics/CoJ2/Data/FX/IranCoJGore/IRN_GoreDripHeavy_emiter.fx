EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 1.8)
	}

	GenType("continous")

	ParticleRate()
	{
		keyf(0, 40)
		keyf(0.6, 30)
		keyf(0.7, 0)
	}

	StartVelocity()
	{
		keyf(0, 110)
	}

	StartVelocityRand()
	{
		keyv(0, 10, 20, 10)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(1)
	}
}
