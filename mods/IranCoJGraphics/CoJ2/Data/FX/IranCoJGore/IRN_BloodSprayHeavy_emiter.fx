EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.4)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 9, 13)
	}

	StartVelocity()
	{
		keyf(0, 420)
	}

	StartVelocityRand()
	{
		keyv(0, 160, 240, 160)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.6)
	}
}
