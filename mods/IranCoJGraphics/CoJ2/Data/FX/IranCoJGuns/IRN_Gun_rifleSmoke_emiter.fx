EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 1)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 6)
	}

	StartVelocity()
	{
		keyf(0, 950)
	}

	StartVelocityRand()
	{
		keyv(0, 142.5, 285, 285)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
